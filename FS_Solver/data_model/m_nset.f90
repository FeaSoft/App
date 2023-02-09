! Description:
! Definition of a node index set.
module m_nset
    implicit none
    
    private
    public t_nset, new_nset
    
    type t_nset
        integer              :: n_nodes    ! number of node indices
        integer, allocatable :: i_nodes(:) ! index of nodes
    contains
        final :: destructor
    end type
    
    interface new_nset
        module procedure :: constructor
    end interface
    
    contains
    
    ! Description:
    ! Node index set constructor.
    type(t_nset) function constructor(n_nodes) result(self)
        integer, intent(in) :: n_nodes ! number of node indices
        self%n_nodes = n_nodes
        allocate(self%i_nodes(self%n_nodes))
    end function
    
    ! Description:
    ! Node index set destructor.
    subroutine destructor(self)
        type(t_nset), intent(inout) :: self
        if (allocated(self%i_nodes)) deallocate(self%i_nodes)
    end subroutine
    
end module
