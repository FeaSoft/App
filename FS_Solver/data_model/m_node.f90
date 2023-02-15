! Description:
! Definition of a finite element node.
module m_node
    implicit none
    
    private
    public t_node, new_node
    
    type t_node
        real                 :: coordinates(3) ! nodal coordinates
        integer, allocatable :: dofs(:)        ! algebraic connectivity (positive number: active DOF; negative number: inactive DOF)
    contains
        final :: destructor
    end type
    
    interface new_node
        module procedure :: constructor
    end interface
    
    contains
    
    ! Description:
    ! Finite element node constructor.
    type(t_node) function constructor(n_dofs, x, y, z) result(self)
        integer, intent(in) :: n_dofs  ! number of DOFs
        real,    intent(in) :: x, y, z ! nodal coordinates
        self%coordinates = [x, y, z]
        allocate(self%dofs(n_dofs))
    end function
    
    ! Description:
    ! Finite element node destructor.
    subroutine destructor(self)
        type(t_node), intent(inout) :: self
        if (allocated(self%dofs)) deallocate(self%dofs)
    end subroutine
    
end module
