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
    type(t_nset) function constructor(n_nodes) result(this)
        integer, intent(in) :: n_nodes ! number of node indices
        this%n_nodes = n_nodes
        allocate(this%i_nodes(this%n_nodes))
    end function
    
    ! Description:
    ! Node index set destructor.
    subroutine destructor(this)
        type(t_nset), intent(inout) :: this
        if (allocated(this%i_nodes)) deallocate(this%i_nodes)
    end subroutine
    
end module
